import numpy as np
import yfinance as yf
import pandas as pd
import math
import logging
from sklearn.linear_model import LinearRegression
from datetime import datetime

Fluctuate = {}

def is_fluctuation(ticker):
    try:
        data = yf.download(
            tickers=ticker,
            interval='1m',
            period='1d',
            progress=False,
            auto_adjust=True,
            group_by='ticker'
        )
    except Exception as e:
        logging.error(f"Download error for {ticker}: {e}")
        return False , 0

    try:
        df = data[ticker][['Open', 'High', 'Low', 'Close']].copy()
    except KeyError:
        logging.warning(f"[{ticker}] Data not found.")
        return False , 0

    # Convert to IST and filter market hours
    try:
        df.index = df.index.tz_convert('Asia/Kolkata')
    except:
        df.index = df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')

    df = df.between_time("09:15", "15:30")

    if df.empty or len(df) < 30:
        logging.warning(f"[{ticker}] Not enough data ({len(df)} rows)")
        return False,0.0

    # Take last 60 candles
    end_index = len(df)
    #start = max(0,end_index-60)
    df_slice = df.iloc[0:end_index]

    # --- Volatility Calculation ---
    returns = df_slice['Close'].pct_change().dropna()
    volatility = returns.std()

    # --- Linear regression ---
    y = df_slice['Close'].values.reshape(-1, 1)
    z = len(y)
    x = np.arange(z).reshape(-1, 1)
    model = LinearRegression().fit(x, y)

    r2 = model.score(x, y)
    slope = model.coef_[0][0]

    # Convert slope to angle
    angle = math.degrees(math.atan(slope))

    # --- Sideways detection ---
    price_range = df_slice['High'].max() - df_slice['Low'].min()
    avg_price = df_slice['Close'].mean()
    range_percent = (price_range / avg_price) * 100

    # --- Time based volatility threshold ---
    now = datetime.now().strftime("%H:%M")

    if now < "10:00":
        vol_threshold = 0.006
    else:
        vol_threshold = 0.004

    # --- Final logic ---
    if (volatility < vol_threshold and r2 >= 0.80 ) :#or (r2 >= 0.92):
        line = (f"{datetime.now().strftime('%H:%M:%S')},{ticker},{volatility:.4f},{angle:.2f},{range_percent:.2f},[{z}],{r2:.2f}")

        with open("Fluctuation.txt", "a", encoding="utf-8") as f:
            f.write(line + "\n")

        return True , r2

    else:
        line = (f"{datetime.now().strftime('%H:%M:%S')},{ticker},{volatility:.4f},{angle:.2f},{range_percent:.2f},[{z}],{r2:.2f}")

        with open("Fluctuation.txt", "a", encoding="utf-8") as f:
            f.write(line + "\n")

        return False , r2


# tickers = ['GABRIEL.NS']#['CHAMBLFERT.NS', 'ABFRL.NS', 'IRISDOREME.NS', 'CAMLINFINE.NS', 'AMBUJACEM.NS', 'ASIANTILES.NS', 'ANANTRAJ.NS', 'DEEPINDS.NS', 'GPIL.NS', 'CCL.NS', 'GIPCL.NS', 'DALBHARAT.NS', 'HERITGFOOD.NS', 'IMFA.NS', 'INDUSINDBK.NS', 'SBC.NS', 'JSWSTEEL.NS', 'INDRAMEDCO.NS', 'GODREJPROP.NS', 'NYKAA.NS', 'JUBLINGREA.NS', 'PATELRMART.NS', 'MINDACORP.NS', 'KOTAKBANK.NS', 'M&MFIN.NS', 'MOTILALOFS.NS', 'NAM-INDIA.NS', 'RAYMOND.NS', 'OBEROIRLTY.NS', 'TDPOWERSYS.NS', 'TIPSMUSIC.NS', 'TORNTPOWER.NS', 'PRESTIGE.NS', 'SWSOLAR.NS', 'SUPREMEIND.NS', 'THELEELA.NS', 'TVSMOTOR.NS', 'V2RETAIL.NS', 'AEGISVOPAK.NS', 'APOLLO.NS', 'ABSLAMC.NS', 'ASHOKLEY.NS', 'CUB.NS', 'CREDITACC.NS', 'DMART.NS', 'ECLERX.NS', 'EXICOM.NS', 'IEX.NS', 'JSWINFRA.NS', 'ORIENTHOT.NS', 'PARKHOTELS.NS', 'SWIGGY.NS', 'WELENT.NS', 'TITAN.NS', 'AEGISLOG.NS', 'BHEL.NS', 'FUSION.NS', 'EFCIL.NS', 'NRBBEARING.NS', 'SHREEJISPG.NS', 'MANYAVAR.NS', 'COROMANDEL.NS', 'ROLEXRINGS.NS', 'INDOTHAI.NS', 'SADHNANIQ.NS', 'GESHIP.NS', 'SANDUMA.NS', 'M&M.NS', 'VINCOFE.NS', 'GMRAIRPORT.NS', 'CELLO.NS', 'HINDZINC.NS', 'LOKESHMACH.NS', 'ETERNAL.NS', 'NATIONALUM.NS', 'SARDAEN.NS', 'SMCGLOBAL.NS', 'GRAVITA.NS', 'VEDL.NS', 'EPL.NS']
# for ticker in tickers:
#     print(is_fluctuation(ticker))
