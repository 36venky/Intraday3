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
        return False ,0

    try:
        df = data[ticker][['Open', 'High', 'Low', 'Close']].copy()
    except KeyError:
        logging.warning(f"[{ticker}] Data not found.")
        return False ,0

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
    r2 = round(r2,2)
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
        return True , r2

    else:
        line = (f"{datetime.now().strftime('%H:%M:%S')},{ticker},{volatility:.4f},{angle:.2f},{range_percent:.2f},[{z}],{r2:.2f}")
        return False , r2


# tickers = ['AARTIPHARM', 'ABDL', 'ABSLAMC', 'AEGISLOG', 'AGARWALEYE', 'AMBUJACEM', 'ANANTRAJ', 'ANTHEM', 'APOLLOTYRE', 'ARSSBL', 'ASHAPURMIN', 'ASTEC', 'ASTERDM', 'ATGL', 'ATHERENERG', 'AVL', 'BALUFORGE', 'BANCOINDIA', 'BANKBEES', 'BBOX', 'BERGEPAINT', 'BIKAJI', 'BLACKBUCK', 'BLUEJET', 'BLUESTONE', 'BORORENEW', 'CAPILLARY', 'CELLO', 'CGPOWER', 'CHOICEIN', 'COHANCE', 'CONCOR', 'DABUR', 'DLF', 'ELGIEQUIP', 'EMAMILTD', 'EUREKAFORB', 'FINCABLES', 'FIVESTAR', 'GALLANTT', 'GHCL', 'GMDCLTD', 'GODREJAGRO', 'GRANULES', 'GRAPHITE', 'HDBFS', 'HDFCLIFE', 'HEG', 'HEXT', 'ICICIPRULI', 'IIFL', 'INDGN', 'INDHOTEL', 'IRCTC', 'JBMA', 'JKIL', 'JKLAKSHMI', 'JSL', 'JSLL', 'JUBLFOOD', 'JUBLINGREA', 'JUNIORBEES', 'KALYANKJIL', 'KEC', 'KIMS', 'KIRIINDUS', 'LANDMARK', 'LICHSGFIN', 'MAHSEAMLES', 'MANYAVAR', 'MARATHON', 'MARICO', 'MINDACORP', 'NAVA', 'ORKLAINDIA', 'OSWALPUMPS', 'PARAS', 'PATANJALI', 'PGEL', 'PICCADIL', 'PNGJL', 'PREMEXPLN', 'PRICOLLTD', 'PROTEAN', 'QPOWER', 'RATEGAIN', 'RAYMONDREL', 'RKFORGE', 'ROSSTECH', 'RUBICON', 'SALZERELEC', 'SANDHAR', 'SCHNEIDER', 'SENORES', 'SHAKTIPUMP', 'SILVERTUC', 'SIRCA', 'SONACOMS', 'STUDDS', 'SUDEEPPHRM', 'SUNTV', 'SYNGENE', 'SYRMA', 'TANLA', 'TATACHEM', 'TATAINVEST', 'TATATECH', 'TDPOWERSYS', 'TEJASNET', 'TIPSMUSIC', 'TMB', 'TRANSRAILL', 'TRITURBINE', 'UPL', 'VARROC', 'VENUSREM', 'WELENT', 'WEWORK', 'YATHARTH', 'ZENSARTECH']#EX.Price.list(125, 150)
# tickers = [t + '.NS' for t in tickers]
# for ticker in tickers:
#     print(is_fluctuation(ticker), ticker)
