from pdb import main
import sys
import time
import yfinance as yf
import logging
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data_Manager import *


# =========================================================
# LOGGING CONFIG
# =========================================================

os.makedirs("logs", exist_ok=True)

logging.basicConfig(

    filename="logs/market_data.log",
    
    level=logging.INFO,

    format="%(asctime)s %(levelname)s %(message)s"
)

# =========================================================
# GLOBAL MARKET DATA
# =========================================================

MARKET_DATA = {}

# =========================================================
# DOWNLOAD FUNCTION
# =========================================================

def Download(tickers):

    global MARKET_DATA

    configs = {

        "1m": "1d",
        "5m": "5d",
        "15m": "15d",
        "1d": "1mo"
    }

    for interval, period in configs.items():

        try:

            data = yf.download(

                tickers=tickers,

                interval=interval,

                period=period,

                progress=False,

                auto_adjust=True,

                group_by='ticker',

                threads=True
            )

        except Exception as e:

            logging.error(
                f"{interval} download error : {e}"
            )

            continue

        for ticker in tickers:

            try:

                # MULTI TICKER
                if len(tickers) > 1:

                    df = data[ticker][
                        ['Open', 'High', 'Low', 'Close']
                    ].copy()

                # SINGLE TICKER
                else:

                    df = data[
                        ['Open', 'High', 'Low', 'Close']
                    ].copy()

            except KeyError:

                logging.warning(
                    f"[{ticker}] {interval} data not found."
                )

                continue

            # =================================================
            # TIMEZONE CONVERSION
            # =================================================

            try:

                df.index = df.index.tz_convert(
                    'Asia/Kolkata'
                )

            except:

                try:

                    df.index = (
                        df.index
                        .tz_localize('UTC')
                        .tz_convert('Asia/Kolkata')
                    )

                except Exception as e:

                    logging.error(
                        f"{ticker} timezone error : {e}"
                    )

            # =================================================
            # MARKET HOURS FILTER
            # =================================================

            if interval in ["1m", "5m", "15m"]:

                df = df.between_time(
                    '09:15',
                    '15:30'
                )

            # =================================================
            # CLEAN DATA
            # =================================================

            df.dropna(inplace=True)

            if df.empty:

                logging.warning(
                    f"[{ticker}] {interval} dataframe empty."
                )

                continue

            # =================================================
            # STORE DATA
            # =================================================

            if ticker not in MARKET_DATA:

                MARKET_DATA[ticker] = {}

            MARKET_DATA[ticker][interval] = df

            logging.info(
                f"[{ticker}] {interval} stored successfully."
            )


def Store(df, ticker, interval):

    global MARKET_DATA

    try:
        # =================================================
        # STORE DATA
        # =================================================

        if ticker not in MARKET_DATA:

            MARKET_DATA[ticker] = {}

        MARKET_DATA[ticker][interval] = df

        logging.info(
            f"[{ticker}] {interval} stored successfully."
        )

    except Exception as e:

        logging.error(
            f"{ticker} store error : {e}"
        )
# =========================================================
# COMMON FETCH FUNCTION
# =========================================================

def get_data(ticker, interval):

    global MARKET_DATA

    try:

        return MARKET_DATA[ticker][interval]

    except KeyError:

        logging.warning(
            f"{ticker} {interval} not available."
        )

        return None

# =========================================================
# PREVIOUS DAY LEVELS
# =========================================================

def previous_day_levels(ticker):

    df = get_data(ticker, "1d")

    if df is None:

        logging.warning(
            f"{ticker} daily data unavailable."
        )

        return None, None

    if len(df) < 2:

        logging.warning(
            f"{ticker} insufficient daily candles."
        )

        return None, None

    prev_day = df.iloc[-2]

    prev_high = prev_day['High']

    prev_low = prev_day['Low']

    logging.info(
        f"{ticker} Prev High: {prev_high}, "
        f"Prev Low: {prev_low}"
    )

    return prev_high, prev_low

# Trail

def main():
    start = time.perf_counter()
    Download(get_ticker(1))
    end = time.perf_counter()

    print(f"Execution Time: {end - start:.2f} seconds")


if __name__ == "__main__":
    main()

